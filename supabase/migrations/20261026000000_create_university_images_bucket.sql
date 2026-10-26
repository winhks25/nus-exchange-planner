-- University photographs: a public bucket for card images.
-- Reads are open through the public URL; writes are restricted to the
-- service role (the administrative uploader). The bucket-level upload
-- restrictions cap the object size and allowed image types.
DO $$
BEGIN
  -- Execute only if Supabase storage schema and tables exist.
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'storage' AND table_name = 'buckets'
  ) THEN
    INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
    VALUES (
      'university-images',
      'university-images',
      true,
      4194304,
      array['image/jpeg', 'image/png', 'image/webp']
    )
    ON CONFLICT (id) DO NOTHING;
  END IF;

  -- Create policies only if storage.objects and service_role role exist.
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'storage' AND table_name = 'objects'
  ) AND EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = 'service_role'
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM pg_policies
      WHERE schemaname = 'storage' AND tablename = 'objects' AND policyname = 'university-images service role insert'
    ) THEN
      CREATE POLICY "university-images service role insert"
        ON storage.objects
        FOR INSERT
        TO service_role
        WITH CHECK (bucket_id = 'university-images');
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM pg_policies
      WHERE schemaname = 'storage' AND tablename = 'objects' AND policyname = 'university-images service role update'
    ) THEN
      CREATE POLICY "university-images service role update"
        ON storage.objects
        FOR UPDATE
        TO service_role
        USING (bucket_id = 'university-images')
        WITH CHECK (bucket_id = 'university-images');
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM pg_policies
      WHERE schemaname = 'storage' AND tablename = 'objects' AND policyname = 'university-images service role select'
    ) THEN
      CREATE POLICY "university-images service role select"
        ON storage.objects
        FOR SELECT
        TO service_role
        USING (bucket_id = 'university-images');
    END IF;
  END IF;
END $$;
